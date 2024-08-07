import { AvatarPage, SchedulePage } from '@pages/shared';
import { MainPage, ExercisePage, TrainPage, SurveyPage } from '@student';
import training from 'assets/sidebar/train.svg';
import schedule from 'assets/sidebar/schedule.svg';
import home from 'assets/sidebar/home.svg';

const studentRouter = [
	{
		path: '/',
		element: <MainPage />,
		img: home
	},
	{
		path: '/train',
		element: <TrainPage />,
		local: 'Тренировки',
		img: training
	},
	{
		path: '/train/:id',
		element: <ExercisePage />
	},
	{
		path: '/schedule',
		element: <SchedulePage />,
		local: 'Расписание',
		img: schedule
	},
	{
		path: '/avatar',
		element: <AvatarPage />
	},
	{
		path: '/survey',
		element: <SurveyPage />,
		local: 'Анкета',
		img: 'feedback'
	}
];

export default studentRouter;
